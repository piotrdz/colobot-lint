#include "NakedNewRule.h"

#include "clang/Tooling/Tooling.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/AST/ExprCXX.h"

using namespace clang;
using namespace clang::ast_matchers;

NakedNewRule::NakedNewRule(MatchFinder& finder,
                                 OutputPrinter& printer)
    : Rule(printer),
      m_matcher(newExpr().bind("new"))
{
    finder.addMatcher(m_matcher, this);
}

void NakedNewRule::run(const MatchFinder::MatchResult& result)
{
    const CXXNewExpr* newExpr = result.Nodes.getNodeAs<CXXNewExpr>("new");
    if (newExpr == nullptr)
        return;

    SourceLocation location = newExpr->getLocStart();
    if (! result.Context->getSourceManager().isInMainFile(location))
        return;

    std::string typeStr = newExpr->getAllocatedType().getAsString();

    m_printer.PrintRuleViolation(
        "naked new",
        Severity::Warning,
        std::string("Naked new called with type '") + typeStr + "'",
        location,
        result.Context->getSourceManager());
}
